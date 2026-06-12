import { BRAND_MARK_PATH, COMPANY_NAME } from "../constants/branding";

export function Watermark() {
  return (
    <div className="app-watermark" aria-hidden="true">
      <div className="watermark-pattern" style={{ backgroundImage: `url("${BRAND_MARK_PATH}")` }} />
      <span className="watermark-caption">{COMPANY_NAME}</span>
    </div>
  );
}
