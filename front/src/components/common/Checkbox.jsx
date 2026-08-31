function Checkbox({ label, id, className = "", ...rest }) {
  return (
    <label className={`checkbox-field ${className}`.trim()} htmlFor={id}>
      <input id={id} type="checkbox" {...rest} />
      {label}
    </label>
  );
}

export default Checkbox;
