import { useEffect, useRef, useState } from "react";

function MultiSelectDropdown({ label, icon, options, selected, onToggle, placeholder }) {
  const [isOpen, setIsOpen] = useState(false);
  const rootRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (rootRef.current && !rootRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const summary = selected.length > 0 ? `${selected.length}개 선택됨` : placeholder;

  return (
    <div className="field multi-select" ref={rootRef}>
      {label && <span className="field-label">{label}</span>}
      <button
        type="button"
        className="select-field multi-select__trigger"
        onClick={() => setIsOpen((prev) => !prev)}
      >
        <span className="multi-select__value">
          {icon && <span className="multi-select__icon">{icon}</span>}
          {summary}
        </span>
        <span className="multi-select__chevron">▾</span>
      </button>

      {isOpen && (
        <div className="multi-select__panel">
          {options.map((option) => (
            <label className="multi-select__option" key={option.code}>
              <input
                type="checkbox"
                checked={selected.includes(option.code)}
                onChange={() => onToggle(option.code)}
              />
              {option.name}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

export default MultiSelectDropdown;
