import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClockRotateLeft, faXmark } from "@fortawesome/free-solid-svg-icons";
import "../../styles/RecentSelections.css";

function RecentSelections({ items, onSelect, onRemove }) {
  if (items.length === 0) return null;

  return (
    <div className="recent-selections">
      <p className="recent-selections__label">
        <FontAwesomeIcon icon={faClockRotateLeft} /> 최근 선택 항목
      </p>
      <ul className="recent-selections__list">
        {items.map((item) => (
          <li className="recent-selections__item" key={item.id}>
            <button
              type="button"
              className="recent-selections__select"
              onClick={() => onSelect(item)}
            >
              {item.label}
            </button>
            <button
              type="button"
              className="recent-selections__remove"
              aria-label="최근 선택 항목 삭제"
              onClick={() => onRemove(item.id)}
            >
              <FontAwesomeIcon icon={faXmark} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default RecentSelections;
