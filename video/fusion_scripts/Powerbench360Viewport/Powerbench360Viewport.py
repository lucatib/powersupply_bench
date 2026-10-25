# Giro 360° catturato dal viewport, con la shell che sfuma e riappare (l'opacità nel viewport funziona).
# Parte dalla vista corrente. Salva un PNG per frame in Videos\powerbench_360_vp.

import adsk.core, adsk.fusion, math, os, time, traceback

FRAMES = 240            # 240 frame a 24 fps = 10 secondi
WIDTH, HEIGHT = 1920, 1080
OUT_DIR = os.path.join(os.path.expanduser('~'), 'Videos', 'powerbench_360_vp')

SHELL_PARTS = ['bodytop', 'bodybot', 'bodyleft', 'bodyright', 'front', 'back']
FADE_OUT = (0.15, 0.35)   # frazione del giro: sfuma fino a sparire
FADE_IN = (0.60, 0.80)    # frazione del giro: riappare del tutto

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.log')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s %s\n' % (time.strftime('%H:%M:%S'), msg))


log('modulo caricato')


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


def smooth(a, b, t):
    x = min(1.0, max(0.0, (t - a) / (b - a)))
    return x * x * (3 - 2 * x)


def shell_opacity(t):
    return 1.0 - smooth(FADE_OUT[0], FADE_OUT[1], t) * (1.0 - smooth(FADE_IN[0], FADE_IN[1], t))


def is_shell_part(name):
    n = name.lower().replace(' ', '').replace('_', '')
    return any(n.startswith(p) for p in SHELL_PARTS)


def find_shell_targets(design):
    # oggetti con proprietà .opacity: componenti non-root e corpi
    root = design.rootComponent
    targets, names = [], []
    for comp in design.allComponents:
        if comp != root and is_shell_part(comp.name):
            targets.append(comp)
            names.append('componente ' + comp.name)
            continue
        for body in comp.bRepBodies:
            if is_shell_part(body.name):
                targets.append(body)
                names.append('corpo %s (in %s)' % (body.name, comp.name))
    return targets, names


def run(context):
    log('run() avviato')
    app = adsk.core.Application.get()
    ui = app.userInterface
    targets, originals = [], []
    ancestors, anc_orig = [], []
    saved_cam = None
    progress = None
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Apri il design del powerbench prima di lanciare lo script.')
            return

        targets, names = find_shell_targets(design)
        if len(targets) < 6:
            log('shell incompleta: ' + '; '.join(names))
            ui.messageBox('Trovati solo %d pezzi della shell (ne servono 6). Vedi run.log.' % len(targets))
            return
        log('shell trovata: ' + '; '.join(names))

        # Anche i componenti che contengono la shell possono avere un'opacità < 1 (ereditata):
        # li porto a 1 durante il giro, così la sfumatura parte da opaco.
        root = design.rootComponent
        ancestors = []
        for t in targets:
            comp = t if isinstance(t, adsk.fusion.Component) else t.parentComponent
            occs = root.allOccurrencesByComponent(comp)
            chain = [comp]
            ctx = occs.item(0).assemblyContext if occs.count else None
            while ctx:
                chain.append(ctx.component)
                ctx = ctx.assemblyContext
            for c in chain:
                if c != root and all(c != a for a in ancestors) and all(c != x for x in targets):
                    ancestors.append(c)
        anc_orig = [a.opacity for a in ancestors]
        log('opacità: ' + '; '.join('%s=%.2f' % (a.name, a.opacity) for a in ancestors)
            + ' | shell: ' + '; '.join('%.2f' % t.opacity for t in targets))
        originals = [t.opacity for t in targets]
        for a in ancestors:
            a.opacity = 1.0

        bb = design.rootComponent.boundingBox
        center = adsk.core.Point3D.create(
            (bb.minPoint.x + bb.maxPoint.x) / 2,
            (bb.minPoint.y + bb.maxPoint.y) / 2,
            (bb.minPoint.z + bb.maxPoint.z) / 2)

        vp = app.activeViewport
        cam = vp.camera
        saved_cam = vp.camera
        up = snap_axis(cam.upVector)
        offset = center.vectorTo(cam.eye)
        cam.isSmoothTransition = False

        os.makedirs(OUT_DIR, exist_ok=True)
        progress = ui.createProgressDialog()
        progress.show('Powerbench360Viewport', 'Frame %v di %m', 0, FRAMES)

        for i in range(FRAMES):
            if progress.wasCancelled:
                log('annullato al frame %d' % i)
                break
            progress.progressValue = i
            alpha = shell_opacity(float(i) / FRAMES)
            for t in targets:
                t.opacity = alpha
            eye = center.copy()
            eye.translateBy(rotate(offset, up, 2 * math.pi * i / FRAMES))
            cam.eye = eye
            cam.target = center
            cam.upVector = up
            vp.camera = cam
            vp.refresh()
            adsk.doEvents()
            if not vp.saveAsImageFile(os.path.join(OUT_DIR, 'frame_%04d.png' % i), WIDTH, HEIGHT):
                log('saveAsImageFile fallito al frame %d' % i)
        progress.hide()
        log('completato')
        ui.messageBox('Fatto: frame in\n%s' % OUT_DIR)
    except:
        log(traceback.format_exc())
        ui.messageBox('Errore:\n{}'.format(traceback.format_exc()))
    finally:
        for t, o in zip(targets, originals):
            try:
                t.opacity = o
            except:
                pass
        for a, o in zip(ancestors, anc_orig):
            try:
                a.opacity = o
            except:
                pass
        try:
            if saved_cam:
                app.activeViewport.camera = saved_cam
        except:
            pass
