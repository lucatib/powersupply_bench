# Esporta tutti i design del progetto cloud "PowerSupply_Bench" come archivi Fusion (.f3d)
# in C:\Workspace\powersupply_bench\models. Non modifica né salva nulla nel cloud:
# i file vengono aperti in background e chiusi SENZA salvare (quelli già aperti restano aperti).

import adsk.core, adsk.fusion, os, re, time, traceback

PROJECT = 'PowerSupply_Bench'
OUT_DIR = r'C:\Workspace\powersupply_bench\models'
LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.log')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s %s\n' % (time.strftime('%H:%M:%S'), msg))


log('modulo caricato')


def collect(folder, rel, out):
    for f in folder.dataFiles:
        if f.fileExtension.lower() in ('f3d', 'f3z'):
            out.append((rel, f))
    for sub in folder.dataFolders:
        collect(sub, os.path.join(rel, sub.name), out)


def safe(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name).strip()


def run(context):
    log('run() avviato')
    app = adsk.core.Application.get()
    ui = app.userInterface
    progress = None
    try:
        proj = None
        for p in app.data.dataProjects:
            if p.name == PROJECT:
                proj = p
        if not proj:
            ui.messageBox('Progetto %s non trovato.' % PROJECT)
            return

        files = []
        collect(proj.rootFolder, '', files)
        log('%d design da esportare' % len(files))

        open_ids = {}
        for d in app.documents:
            try:
                if d.dataFile:
                    open_ids[d.dataFile.id] = d
            except:
                pass

        progress = ui.createProgressDialog()
        progress.show('ExportPowerSupply', 'File %v di %m', 0, len(files))
        ok, failed = 0, []
        for n, (rel, df) in enumerate(files):
            if progress.wasCancelled:
                log('annullato')
                break
            progress.progressValue = n
            name = '%s.f3d' % safe(df.name)
            dest_dir = os.path.join(OUT_DIR, rel)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, name)
            t0 = time.time()
            doc, was_open = None, df.id in open_ids
            try:
                doc = open_ids[df.id] if was_open else app.documents.open(df, False)
                design = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
                opts = design.exportManager.createFusionArchiveExportOptions(dest)
                if design.exportManager.execute(opts):
                    ok += 1
                    log('OK %s %.1f MB in %.0fs%s' % (name, os.path.getsize(dest) / 1048576.0,
                                                    time.time() - t0, ' (già aperto)' if was_open else ''))
                else:
                    failed.append(name)
                    log('FALLITO %s' % name)
            except:
                failed.append(name)
                log('ERRORE %s\n%s' % (name, traceback.format_exc()))
            finally:
                if doc and not was_open:
                    try:
                        doc.close(False)
                    except:
                        log('chiusura fallita: %s' % name)
        progress.hide()
        log('finito: %d ok, %d falliti %s' % (ok, len(failed), failed))
        ui.messageBox('Esportati %d di %d design in\n%s\n%s'
                      % (ok, len(files), OUT_DIR, ('Falliti: ' + ', '.join(failed)) if failed else ''))
    except:
        log(traceback.format_exc())
        ui.messageBox('Errore:\n{}'.format(traceback.format_exc()))
