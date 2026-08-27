function Select({ label, id, icon, options, placeholder, className = "", ...rest }) {
  return (
    <div className="field">
      {label && (
        <label className="field-label" htmlFor={id}>
          {label}
        </label>
      )}
      <div className={`text-field-wrap ${icon ? "has-icon" : ""}`.trim()}>
        {icon && <span className="text-field-icon">{icon}</span>}
        <select id={id} className={`select-field ${className}`.trim()} {...rest}>
          {placeholder && (
            <option value="" disabled hidden>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.code ?? option.value} value={option.code ?? option.value}>
              {option.name ?? option.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export default Select;
