function CategoryToggleGroup({ options, selected, onToggle }) {
  return (
    <div className="toggle-group">
      {options.map((option) => {
        const isSelected = selected.includes(option.code);
        return (
          <button
            type="button"
            key={option.code}
            className={`toggle-chip ${isSelected ? "is-selected" : ""}`.trim()}
            onClick={() => onToggle(option.code)}
          >
            {option.name}
          </button>
        );
      })}
    </div>
  );
}

export default CategoryToggleGroup;
