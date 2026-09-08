import { forwardRef } from "react";

const TextField = forwardRef(function TextField(
  { label, id, icon, rightIcon, error, className = "", ...rest },
  ref,
) {
  return (
    <div className="field">
      {label && (
        <label className="field-label" htmlFor={id}>
          {label}
        </label>
      )}
      <div
        className={`text-field-wrap ${icon ? "has-icon" : ""} ${
          rightIcon ? "has-right-icon" : ""
        }`.trim()}
      >
        {icon && <span className="text-field-icon">{icon}</span>}
        <input ref={ref} id={id} className={`text-field ${className}`.trim()} {...rest} />
        {rightIcon && (
          <span className="text-field-icon text-field-icon--right">{rightIcon}</span>
        )}
      </div>
      {error && <span style={{ color: "var(--color-danger-text)", fontSize: 12 }}>{error}</span>}
    </div>
  );
});

export default TextField;
