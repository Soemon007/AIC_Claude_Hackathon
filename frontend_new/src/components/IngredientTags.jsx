export default function IngredientTags({ setInput }) {
  const tags = [
    "Quinoa, Chickpeas",
    "Salmon, Asparagus",
    "Greek Yogurt, Berries"
  ];

  return (
    <div className="input-tags">
      {tags.map((tag) => (
        <span
          key={tag}
          className="tag"
          onClick={() => setInput(tag)}
        >
          {tag}
        </span>
      ))}
    </div>
  );
}