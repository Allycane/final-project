function Tag({ children, onRemove }) {
  return (
    <span className="tag">
      {children}
      {onRemove && (
        <button type="button" className="tag-remove" onClick={onRemove} aria-label="삭제">
          ×
        </button>
      )}
    </span>
  );
}

export default Tag;
