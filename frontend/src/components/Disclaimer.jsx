// REQ-SAFE-01/02/03, REQ-QUERY-09, BR-02: shown wherever generated legal information appears.
export const DISCLAIMER_TEXT =
  'This information is for general informational purposes and is not a substitute for advice from a qualified lawyer. It does not guarantee any legal outcome. Laws change – please verify with authoritative sources.';

export default function Disclaimer({ children = DISCLAIMER_TEXT }) {
  return (
    <div className="disclaimer" role="note">
      <strong>Disclaimer: </strong>
      {children}
    </div>
  );
}
