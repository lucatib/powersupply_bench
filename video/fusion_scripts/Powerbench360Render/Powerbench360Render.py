# Giro 360° lento con dissolvenza della shell: renderizza i frame veri, in due passate.
#   1) shell visibile  -> Videos\powerbench_360_r216
#   2) shell nascosta (solo dove serve) -> Videos\powerbench_360_r216_hidden
# La sfumatura tra le due serie la fa ffmpeg. I frame già presenti vengono saltati.

import adsk.core, adsk.fusion, math, os, time, traceback

FRAMES = 216            # 216 frame a 24 fps = 9 secondi
QUALITY = 40            # uguale alle passate precedenti (frame riusati)
RESOLUTION = adsk.fusion.RenderResolutions.Video1280x720RenderResolution
VIDEOS = os.path.join(os.path.expanduser('~'), 'Videos')
DIR_A = os.path.join(VIDEOS, 'powerbench_360_s216')
DIR_B = os.path.join(VIDEOS, 'powerbench_360_s216_hidden')

# Camera deterministica: elevazione e distanza fissate qui, solo la direzione orizzontale
# di partenza viene presa dalla vista corrente. Così tutti i frame hanno la stessa inquadratura.
ELEVATION_DEG = 22.0
FIT = 1.15              # >1 = modello più piccolo nell'inquadratura

SHELL_PARTS = ['bodytop', 'bodybot', 'bodyleft', 'bodyright', 'front', 'back']
FADE_OUT = (0.15, 0.35)
FADE_IN = (0.60, 0.80)

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.log')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s %s\n' % (time.strftime('%H:%M:%S'), msg))


log('modulo caricato (giro lento 216)')


def snap_axis(v):
    comps = [v.x, v.y, v.z]
    i = max(range(3), key=lambda k: abs(comps[k]))
    axis = [0.0, 0.0, 0.0]
    axis[i] = 1.0 if comps[i] > 0 else -1.0
    return adsk.core.Vector3D.create(*axis)


def rotate(v, k, theta):
    c, s = math.cos(theta), math.sin(theta)
    cross = k.crossProduct(v)
    dot = k.dotProduct(v)
    return adsk.core.Vector3D.create(
        v.x * c + cross.x * s + k.x * dot * (1 - c),
        v.y * c + cross.y * s + k.y * dot * (1 - c),
        v.z * c + cross.z * s + k.z * dot * (1 - c))


def is_shell_part(name):
    n = name.lower().replace(' ', '').replace('_', '')
    return any(n.startswith(p) for p in SHELL_PARTS)


def find_shell_items(design):
    root = design.rootComponent
    items, names = [], []
    for comp in design.allComponents:
        if comp != root and is_shell_part(comp.name):
            for occ in root.allOccurrencesByComponent(comp):
                items.append(occ)
                names.append('occorrenza ' + occ.name)
            continue
        for body in comp.bRepBodies:
            if is_shell_part(body.name):
                items.append(body)
                names.append('corpo %s (in %s)' % (body.name, comp.name))
    return items, names


def run(context):
    log('run() avviato')
    app = adsk.core.Application.get()
    ui = app.userInterface
    items, originals = [], []
    saved_cam = None
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Apri il design del powerbench prima di lanciare lo script.')
            return

        items, names = find_shell_items(design)
        if len(items) < 6:
            log('shell incompleta: ' + '; '.join(names))
            ui.messageBox('Trovati solo %d pezzi della shell (ne servono 6). Vedi run.log.' % len(items))
            return
        log('shell trovata: ' + '; '.join(names))
        originals = [it.isLightBulbOn for it in items]

        bb = design.rootComponent.boundingBox
        center = adsk.core.Point3D.create(
            (bb.minPoint.x + bb.maxPoint.x) / 2,
            (bb.minPoint.y + bb.maxPoint.y) / 2,
            (bb.minPoint.z + bb.maxPoint.z) / 2)

        cur = app.activeViewport.camera
        saved_cam = cur
        up = snap_axis(cur.upVector)
        # direzione orizzontale di partenza = proiezione della vista corrente sul piano orizzontale
        v = center.vectorTo(cur.eye)
        d = v.dotProduct(up)
        h = adsk.core.Vector3D.create(v.x - up.x * d, v.y - up.y * d, v.z - up.z * d)
        h.normalize()
        diag = bb.minPoint.distanceTo(bb.maxPoint)
        fov = cur.perspectiveAngle if cur.cameraType == adsk.core.CameraTypes.PerspectiveCameraType else 0.6
        dist = FIT * diag / (2 * math.tan(fov / 2))
        el = math.radians(ELEVATION_DEG)
        offset = adsk.core.Vector3D.create(
            dist * (math.cos(el) * h.x + math.sin(el) * up.x),
            dist * (math.cos(el) * h.y + math.sin(el) * up.y),
            dist * (math.cos(el) * h.z + math.sin(el) * up.z))
        log('camera: dist=%.2f diag=%.2f fov=%.3f el=%.0f h=(%.4f, %.4f, %.4f)'
            % (dist, diag, fov, ELEVATION_DEG, h.x, h.y, h.z))

        rendering = design.renderManager.rendering
        rendering.resolution = RESOLUTION
        rendering.renderQuality = QUALITY
        rendering.isBackgroundTransparent = False

        first = int(math.floor(FADE_OUT[0] * FRAMES))
        last = int(math.ceil(FADE_IN[1] * FRAMES))
        os.makedirs(DIR_A, exist_ok=True)
        os.makedirs(DIR_B, exist_ok=True)

        def queue(indices, out_dir):
            n = 0
            for i in indices:
                path = os.path.join(out_dir, 'frame_%04d.png' % i)
                if os.path.exists(path):
                    continue
                cam = app.activeViewport.camera
                eye = center.copy()
                eye.translateBy(rotate(offset, up, 2 * math.pi * i / FRAMES))
                cam.eye = eye
                cam.target = center
                cam.upVector = up
                app.activeViewport.camera = cam
                adsk.doEvents()
                if rendering.startLocalRender(path, cam):
                    n += 1
                else:
                    log('startLocalRender fallito al frame %d' % i)
                adsk.doEvents()
            return n

        # Passata 1: shell visibile
        for it, o in zip(items, originals):
            it.isLightBulbOn = o
        adsk.doEvents()
        na = queue(range(FRAMES), DIR_A)
        log('passata A in coda: %d' % na)

        # Passata 2: shell nascosta
        for it in items:
            it.isLightBulbOn = False
        adsk.doEvents()
        nb = queue(range(first, last + 1), DIR_B)
        log('passata B in coda: %d' % nb)

        ui.messageBox('In coda: %d render (shell visibile) + %d (shell nascosta).\n'
                      'Lascia Fusion aperto finché non finiscono.' % (na, nb))
    except:
        log(traceback.format_exc())
        ui.messageBox('Errore:\n{}'.format(traceback.format_exc()))
    finally:
        for it, o in zip(items, originals):
            try:
                it.isLightBulbOn = o
            except:
                pass
        try:
            if saved_cam:
                app.activeViewport.camera = saved_cam
        except:
            pass
