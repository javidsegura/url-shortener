import { useEffect, useMemo, useRef, useState } from "react";
import { config } from "../core/config";
import { useAuth } from "../hooks/useAuth";

type ApiSuccess = {
  // server should return this; supports a few fallbacks just in case
  return_shortened_url?: string;
  shortened_url?: string;
  slug?: string;
  code?: string;
  [key: string]: any;
};

type ApiError = {
  message?: string;
  detail?: string;
  error?: string;
  [key: string]: any;
};

export default function URLLink() {
  const [user, isLoadingAuth] = useAuth();

  const [originalUrl, setOriginalUrl] = useState("");
  const [expiresIn, setExpiresIn] = useState<string>("");
  const [touched, setTouched] = useState<{ url?: boolean; exp?: boolean }>({});

  const [loading, setLoading] = useState(false);
  const [serverSuccess, setServerSuccess] = useState<ApiSuccess | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);

  const urlInputRef = useRef<HTMLInputElement>(null);
  const expInputRef = useRef<HTMLInputElement>(null);

  // ---------- validation ----------
  const urlError = useMemo(() => {
    if (!touched.url && originalUrl === "") return "";
    if (!originalUrl) return "URL is required.";
    try {
      const u = new URL(originalUrl);
      if (u.protocol !== "http:" && u.protocol !== "https:")
        return "Only http:// or https:// URLs are allowed.";
      return "";
    } catch {
      return "Enter a valid URL (e.g., https://example.com/path).";
    }
  }, [originalUrl, touched.url]);

  const expError = useMemo(() => {
    if (!touched.exp && expiresIn === "") return "";
    if (expiresIn === "") return "Expiration is required.";
    const n = Number(expiresIn);
    if (!Number.isInteger(n)) return "Expiration must be an integer number of minutes.";
    if (n < 1) return "Expiration must be at least 1 minute.";
    if (n > 10080) return "Expiration cannot exceed 10080 minutes (7 days).";
    return "";
  }, [expiresIn, touched.exp]);

  const formValid = urlError === "" && expError === "" && originalUrl !== "" && expiresIn !== "";

  // ---------- shareable link ----------
  const shareCode = useMemo(() => {
    if (!serverSuccess) return null;
    // Prefer the field you specified; gracefully fall back to common names
    return (
      serverSuccess.return_shortened_url ??
      serverSuccess.shortened_url ??
      serverSuccess.slug ??
      serverSuccess.code ??
      null
    );
  }, [serverSuccess]);

  const shareableLink = useMemo(() => {
    if (!shareCode) return null;
    // Build shareable as requested
    return `http://localhost/short/${shareCode}`;
  }, [shareCode]);

  // ---------- submit ----------
  const handle_form_submission = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setTouched({ url: true, exp: true });
    setServerError(null);
    setServerSuccess(null);

    if (!formValid) {
      // focus first invalid
      if (urlError) urlInputRef.current?.focus();
      else if (expError) expInputRef.current?.focus();
      return;
    }

    if (!user && !isLoadingAuth) {
      setServerError("You must be logged in to shorten URLs.");
      return;
    }

    setLoading(true);
    try {
      const token = await user?.getIdToken?.();

      const response = await fetch(new URL("link", config.BASE_API_URL).href, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          original_url: originalUrl,
          expires_in: Number(expiresIn),
        }),
      });

      const text = await response.text();
      let payload: any = null;
      try {
        payload = text ? JSON.parse(text) : null;
      } catch {
        // non-JSON response from server
      }

      if (!response.ok) {
        const err = (payload as ApiError) || {};
        const msg =
          err.message ||
          err.detail ||
          err.error ||
          `Request failed with status ${response.status}`;
        throw new Error(msg);
      }

      setServerSuccess(payload as ApiSuccess);
    } catch (e: any) {
      setServerError(e?.message || "Unexpected error. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  // ---------- helpers ----------
  const copyToClipboard = async () => {
    if (!shareableLink) return;
    try {
      await navigator.clipboard.writeText(shareableLink);
      // quick visual confirmation without bringing in a toast lib
      setServerError(null);
      setServerSuccess((prev) => ({ ...(prev || {}), copied: true }));
      setTimeout(() => {
        setServerSuccess((prev) => (prev ? { ...prev, copied: false } : prev));
      }, 1500);
    } catch {
      setServerError("Couldn't copy to clipboard. Please copy manually.");
    }
  };

  // ---------- UI ----------
  return (
    <div className="mx-auto max-w-3xl">
      <div className="bg-white shadow-md rounded-lg p-6">
        <h1 className="text-2xl font-semibold text-gray-800 mb-1">Shorten a URL</h1>
        <p className="text-gray-600 mb-6">
          Enter a full URL and how long it should stay active. Both fields are required.
        </p>

        <form onSubmit={handle_form_submission} noValidate className="space-y-5">
          {/* URL */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="original_url">
              URL link <span className="text-red-600">*</span>
            </label>
            <input
              ref={urlInputRef}
              id="original_url"
              name="original_url"
              type="url"
              inputMode="url"
              placeholder="https://example.com/very/long/link"
              className={`w-full rounded-md border px-3 py-2 outline-none transition focus:ring-2 focus:ring-blue-500 ${
                urlError ? "border-red-500" : "border-gray-300"
              }`}
              value={originalUrl}
              onChange={(e) => setOriginalUrl(e.target.value)}
              onBlur={() => setTouched((t) => ({ ...t, url: true }))}
              aria-invalid={!!urlError}
              required
            />
            {urlError && <p className="mt-1 text-sm text-red-600">{urlError}</p>}
          </div>

          {/* Expires In */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="expires_in">
              Expires in (minutes) <span className="text-red-600">*</span>
            </label>
            <input
              ref={expInputRef}
              id="expires_in"
              name="expires_in"
              type="number"
              inputMode="numeric"
              placeholder="e.g., 60"
              className={`w-56 rounded-md border px-3 py-2 outline-none transition focus:ring-2 focus:ring-blue-500 ${
                expError ? "border-red-500" : "border-gray-300"
              }`}
              value={expiresIn}
              onChange={(e) => setExpiresIn(e.target.value)}
              onBlur={() => setTouched((t) => ({ ...t, exp: true }))}
              min={1}
              max={10080}
              step={1}
              aria-invalid={!!expError}
              required
            />
            <p className="mt-1 text-xs text-gray-500">Allowed: 1 — 10080 (7 days)</p>
            {expError && <p className="mt-1 text-sm text-red-600">{expError}</p>}
          </div>

          {/* Submit */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={!formValid || loading || isLoadingAuth}
              className={`inline-flex items-center justify-center rounded-lg px-5 py-2.5 font-semibold text-white transition ${
                !formValid || loading || isLoadingAuth
                  ? "bg-blue-300 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-700"
              }`}
            >
              {loading ? "Shortening..." : "Shorten URL"}
            </button>
          </div>
        </form>

        {/* Messages */}
        <div className="mt-6 space-y-3" id="endpoints_response">
          {serverError && (
            <div className="rounded-md border border-red-300 bg-red-50 p-4 text-red-700">
              <p className="font-medium">Error</p>
              <p className="text-sm">{serverError}</p>
            </div>
          )}

          {serverSuccess && (
            <div className="rounded-md border border-green-300 bg-green-50 p-4 text-green-700">
              <p className="font-medium mb-2">Success</p>

              {/* Show any server message if present */}
              {"message" in serverSuccess && serverSuccess.message && (
                <p className="text-sm mb-2">{String(serverSuccess.message)}</p>
              )}

              {shareableLink ? (
                <div className="flex flex-col sm:flex-row sm:items-center sm:gap-3">
                  <a
                    href={shareableLink}
                    target="_blank"
                    rel="noreferrer"
                    className="break-all underline text-blue-700"
                  >
                    {shareableLink}
                  </a>
                  <button
                    onClick={copyToClipboard}
                    className="mt-2 sm:mt-0 inline-flex items-center justify-center rounded-md bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 text-sm font-medium transition"
                    type="button"
                  >
                    Copy
                  </button>
                </div>
              ) : (
                <p className="text-sm">
                  Shortened link created, but the response didn’t include{" "}
                  <code>return_shortened_url</code>. Check server response below.
                </p>
              )}

              {/* Always show raw payload for transparency/debugging */}
              <details className="mt-3">
                <summary className="cursor-pointer text-sm underline">Show server response</summary>
                <pre className="mt-2 text-xs text-gray-800 bg-white rounded p-3 border border-gray-200 overflow-auto">
                  {JSON.stringify(serverSuccess, null, 2)}
                </pre>
              </details>

              {"copied" in serverSuccess && serverSuccess.copied && (
                <p className="mt-2 text-sm text-green-700">Copied to clipboard!</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
