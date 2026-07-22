LMU Consistency Coach – Version 0.4.8.4 Beta
============================================

Inhalt dieses Archivs (in Repo-Struktur – einfach ueber deinen Arbeitsordner
entpacken und ueberschreiben lassen):

  main.py                          -> Projektwurzel (ersetzen)
  deploy_0_4_8_4.bat               -> Projektwurzel (neu)
  .github/workflows/release.yml    -> ersetzen
  installer/setup.iss              -> ersetzen
  tools/fetch_piper.py             -> OPTIONAL (siehe unten), neu

NICHT enthalten, weil unveraendert:
  tts.py  -> bleibt wie gehabt. _app_dir() + Auto-Erkennung von piper/ sind
             bereits korrekt, keine Aenderung noetig.


Was ist neu in 0.4.8.4
----------------------
1) LIVE-COACHING (main.py)
   - Bei Rundenende wird EIN kurzer deutscher Coach-Satz gebaut (Gemini, mit
     Offline-Fallback aus Delta/Hinweis) und per TTS/Piper ausgegeben –
     getimt auf der Geraden (Vollgas, keine Bremse, Lenkung mittig, >=120 km/h,
     nicht in der Box), max. ein Satz pro Runde, 8 s Cooldown.
   - Opt-in, Default AUS. Umschalten: Menue "Mehr" -> "Live-Coach
     (Sprachhinweise)" oder Hotkey F11.

2) HELLES DESIGN richtig gebaut (main.py)
   - Dashboard-Kacheln, Ziel-Rundenzeit und das KI-Analyse-Fenster folgen jetzt
     dem Theme (vorher hart dunkel). Live-Umschaltung inklusive.

3) HEADER-FIX (main.py)
   - Fenstertitel loest die Version korrekt auf; doppelter Untertitel entfernt.

4) PIPER-STIMME zuverlaessig mitinstallieren (release.yml + setup.iss)
   - release.yml: deutsche Stimme jetzt Thorsten HIGH vom festen Tag v1.0.0;
     continue-on-error entfernt; Fail-Loud-Check (kein Release ohne Stimme).
   - setup.iss: zusaetzlicher [Files]-Eintrag installiert piper/ direkt aus dem
     CI-Ordner nach {app}\piper – spec-unabhaengig. tts.py erkennt es automatisch.


Rollout
-------
Im frischen 0.4.8.4-Ordner deploy_0_4_8_4.bat doppelklicken
(Force-Push main + Tag v0.4.8.4 -> CI baut den Installer).
Braucht git + GitHub CLI (gh, Browser-Login).


Zwei Hinweise
-------------
- tools/fetch_piper.py wird fuer die Pipeline NICHT benoetigt (release.yml laedt
  Piper/Stimme inline). Es ist nur eine robustere Alternative (Verifikation,
  idempotent), falls du spaeter darauf umstellen willst. Kannst du auch weglassen.
- installer/lmu_coach.spec (PyInstaller) lag mir nicht vor. Falls der Spec piper/
  ohnehin schon buendelt, entsteht eine harmlose Doppelung ({app}\piper und
  {app}\_internal\piper; piper/ gewinnt). Wenn du den Spec schickst, sage ich dir,
  ob und wo eine Quelle gestrichen werden kann.
