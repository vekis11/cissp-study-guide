import { useEffect, useState } from "react";

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
}

function isIos(): boolean {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) && !(window as unknown as { MSStream?: unknown }).MSStream;
}

function isStandalone(): boolean {
  return (
    window.matchMedia("(display-mode: standalone)").matches ||
    (navigator as Navigator & { standalone?: boolean }).standalone === true
  );
}

export function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null);
  const [dismissed, setDismissed] = useState(() => localStorage.getItem("pwa-install-dismissed") === "1");
  const [showIosHelp, setShowIosHelp] = useState(false);

  useEffect(() => {
    if (isStandalone()) return;

    const handler = (e: Event) => {
      e.preventDefault();
      setDeferred(e as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", handler);
    return () => window.removeEventListener("beforeinstallprompt", handler);
  }, []);

  if (isStandalone() || dismissed) return null;

  const install = async () => {
    if (deferred) {
      await deferred.prompt();
      await deferred.userChoice;
      setDeferred(null);
      setDismissed(true);
      localStorage.setItem("pwa-install-dismissed", "1");
      return;
    }
    if (isIos()) {
      setShowIosHelp(true);
    }
  };

  const showBanner = deferred || isIos();

  if (!showBanner && !showIosHelp) return null;

  return (
    <div className="install-banner">
      <div className="install-banner-inner">
        <div>
          <strong>Install daily companion</strong>
          <p className="install-sub">
            {showIosHelp
              ? "Tap Share → Add to Home Screen in Safari to install on iPhone/iPad."
              : "Add to your home screen for offline-ready study on Android, PC, or iPhone."}
          </p>
        </div>
        <div className="install-actions">
          {!showIosHelp && (
            <button type="button" className="btn btn-primary btn-sm" onClick={install}>
              Install App
            </button>
          )}
          {isIos() && !showIosHelp && (
            <button type="button" className="btn btn-secondary btn-sm" onClick={() => setShowIosHelp(true)}>
              iPhone help
            </button>
          )}
          <button
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setDismissed(true);
              localStorage.setItem("pwa-install-dismissed", "1");
            }}
          >
            Later
          </button>
        </div>
      </div>
    </div>
  );
}
