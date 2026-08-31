function TextField({ label, id, icon, error, className = "", ...rest }) {
  return (
    <div className="field">
      {label && (
        <label className="field-label" htmlFor={id}>
          {label}
        </label>
      )}
      <div className={`text-field-wrap ${icon ? "has-icon" : ""}`.trim()}>
        {icon && <span className="text-field-icon">{icon}</span>}
        <input id={id} className={`text-field ${className}`.trim()} {...rest} />
      </div>
      {error && <span style={{ color: "var(--color-danger-text)", fontSize: 12 }}>{error}</span>}
    </div>
  );
}

export default TextField;
