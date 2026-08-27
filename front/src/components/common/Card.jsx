function Card({ children, className = "", style, ...rest }) {
  return (
    <div className={`card ${className}`.trim()} style={style} {...rest}>
      {children}
    </div>
  );
}

export default Card;
