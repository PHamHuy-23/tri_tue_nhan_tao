import { colors } from "../theme/colors";

interface Props {
  label: string;
  onClick: () => void;
  active?: boolean;
  small?: boolean;
}

export function PixelButton({ label, onClick, active, small }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="pixel-shadow pixel-border"
      style={{
        background: active ? colors.accent : colors.panel,
        color: active ? colors.bg : colors.text,
        padding: small ? "8px 12px" : "12px 16px",
        fontSize: small ? 8 : 10,
        borderColor: colors.line,
        transform: "translate(-2px, -2px)",
      }}
    >
      {label}
    </button>
  );
}
