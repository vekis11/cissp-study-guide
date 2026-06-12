import { TEMTECH_LOGO_URL, COMPANY_NAME } from "../constants/branding";

export function Watermark() {
  return (
    <div className="app-watermark" aria-hidden="true">
      <div
        className="watermark-pattern"
        style={{ backgroundImage: `url("${TEMTECH_LOGO_URL}")` }}
      />
      <span className="watermark-caption">{COMPANY_NAME}</span>
    </div>
  );
}
