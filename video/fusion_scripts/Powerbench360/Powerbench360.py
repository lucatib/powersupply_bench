# Rotazione 360° della camera attorno al modello attivo, salva un PNG per frame.
# Inquadra il modello come preferisci (distanza e altezza), poi lancia lo script:
# la camera ruota attorno all'asse verticale partendo dalla vista corrente.

import adsk.core, adsk.fusion, math, os, traceback

FRAMES = 240            # 240 frame a 30 fps = 8 secondi
WIDTH, HEIGHT = 1920, 1080
OUT_DIR = os.path.join(os.path.expanduser('~'), 'Desktop', 'powerbench_360')
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.log')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(msg + '\n')


log('modulo caricato')


def snap_axis(v):
    # Asse mondo più vicino all'up vector della camera (Y-up o Z-up)
    comps = [v.x, v.y, v.z]
    i = max(range(3), key=lambda k: abs(comps[k]))
    axis = [0.0, 0.0, 0.0]
    axis[i] = 1.0 if comps[i] > 0 else -1.0
    return adsk.core.Vector3D.create(*axis)


def rotate(v, k, theta):
    # Rodrigues: ruota v attorno all'asse unitario k
    c, s = math.cos(theta), math.sin(theta)
    cross = k.crossProduct(v)
    dot = k.dotProduct(v)
    return adsk.core.Vector3D.create(
        v.x * c + cross.x * s + k.x * dot * (1 - c),
        v.y * c + cross.y * s + k.y * dot * (1 - c),
        v.z * c + cross.z * s + k.z * dot * (1 - c))


def run(context):
    log('run() avviato')
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        ui.messageBox('Powerbench360: avvio rotazione 360°, %d frame.\nNon toccare Fusion fino al messaggio finale.' % FRAMES)
        design = adsk.fusion.Design.cast(app.activeProduct)
        log('prodotto attivo: %s' % (app.activeProduct.productType if app.activeProduct else None))
        if not design:
            ui.messageBox('Apri il design del powerbench prima di lanciare lo script.')
            return

        bb = design.rootComponent.boundingBox
        center = adsk.core.Point3D.create(
            (bb.minPoint.x + bb.maxPoint.x) / 2,
            (bb.minPoint.y + bb.maxPoint.y) / 2,
            (bb.minPoint.z + bb.maxPoint.z) / 2)

        vp = app.activeViewport
        cam = vp.camera
        up = snap_axis(cam.upVector)
        offset = center.vectorTo(cam.eye)

        os.makedirs(OUT_DIR, exist_ok=True)
        log('output: %s' % OUT_DIR)
        cam.isSmoothTransition = False

        progress = ui.createProgressDialog()
        progress.show('Powerbench360', 'Frame %v di %m', 0, FRAMES)
        for i in range(FRAMES):
            if progress.wasCancelled:
                break
            progress.progressValue = i
            v = rotate(offset, up, 2 * math.pi * i / FRAMES)
            eye = center.copy()
            eye.translateBy(v)
            cam.eye = eye
            cam.target = center
            cam.upVector = up
            vp.camera = cam
            vp.refresh()
            adsk.doEvents()
            ok = vp.saveAsImageFile(os.path.join(OUT_DIR, 'frame_%04d.png' % i), WIDTH, HEIGHT)
            if not ok:
                log('saveAsImageFile fallito al frame %d' % i)
        progress.hide()

        log('completato')
        ui.messageBox('Fatto: frame salvati in\n%s' % OUT_DIR)
    except:
        log(traceback.format_exc())
        ui.messageBox('Errore:\n{}'.format(traceback.format_exc()))
