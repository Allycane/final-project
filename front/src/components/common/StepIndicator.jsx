function StepIndicator({ steps, currentStep }) {
  return (
    <div className="step-indicator">
      {steps.map((label, index) => {
        const stepNumber = index + 1;
        const isDone = stepNumber < currentStep;
        const isActive = stepNumber === currentStep;

        return (
          <div className="step-indicator__step" key={label}>
            <div
              className={`step-indicator__step ${isActive ? "is-active" : ""} ${
                isDone ? "is-done" : ""
              }`.trim()}
            >
              <span className="step-indicator__circle">{stepNumber}</span>
              <span className="step-indicator__label">{label}</span>
            </div>
            {stepNumber < steps.length && (
              <span className={`step-indicator__bar ${isDone ? "is-done" : ""}`.trim()} />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default StepIndicator;
