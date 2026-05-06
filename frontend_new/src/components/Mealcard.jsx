function renderList(items, renderItem) {
  if (!items?.length) {
    return null;
  }

  return items.map(renderItem);
}

function FeedbackRow() {
  return (
    <div className="feedback-row">
      <button className="feedback-btn" type="button" aria-label="Thumbs up">
        👍
      </button>
      <button className="feedback-btn" type="button" aria-label="Thumbs down">
        👎
      </button>
    </div>
  );
}

export default function MealCard({ result, error, loading }) {
  if (loading) {
    return (
      <div className="response-area">
        <div className="meal-card">
          <h4>Building Recommendation</h4>
          <p>Analyzing ingredients and tailoring a PCOS-friendly meal.</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="response-area">
        <div className="meal-card error-card">
          <h4>We hit a snag</h4>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!result) {
    return null;
  }

  if (typeof result === "string") {
    return (
      <div className="response-area">
        <div className="meal-card">
          <h4>Recommended Meal</h4>
          <p>{result}</p>
        </div>
        <FeedbackRow />
      </div>
    );
  }

  const {
    title,
    description,
    ingredients = [],
    recipe_steps: recipeSteps = [],
    recommendation_context: context,
  } = result;

  return (
    <div className="response-area">
      <div className="meal-card">
        <h4>Recommended Meal</h4>
        <h3 className="meal-title">{title}</h3>
        <p className="meal-description">{description}</p>

        {!!context && (
          <div className="meal-meta">
            <span className="meta-pill">{context.goal}</span>
            <span className="meta-pill">
              Risk level: {context.risk_level}
            </span>
            {renderList(context.macro_focus, (item) => (
              <span key={item} className="meta-pill subtle">
                {item}
              </span>
            ))}
          </div>
        )}

        <div className="meal-grid">
          <div>
            <h5>Ingredients</h5>
            <ul className="meal-list">
              {renderList(ingredients, (item) => (
                <li key={item.id || item.label}>{item.label}</li>
              ))}
            </ul>
          </div>

          <div>
            <h5>Method</h5>
            <ol className="meal-steps">
              {renderList(recipeSteps, (step) => (
                <li key={step.step || step.instruction}>{step.instruction}</li>
              ))}
            </ol>
          </div>
        </div>

        {!!context && context.avoid?.length > 0 && (
          <div className="recommendation-section">
            <h5>Limit or Avoid</h5>
            <p>{context.avoid.join(", ")}</p>
          </div>
        )}

        {!!context?.user_profile?.validation_notes?.length && (
          <div className="recommendation-section warning-section">
            <h5>Profile Check</h5>
            <p>
              Some profile values look outside a typical range:{" "}
              {context.user_profile.validation_notes.join(", ")}.
            </p>
          </div>
        )}
      </div>
      <FeedbackRow />
    </div>
  );
}
