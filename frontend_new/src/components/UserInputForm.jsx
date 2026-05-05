export default function UserInputForm({
  input,
  setInput,
  onSubmit,
  loading,
}) {
  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form className="input-bar" onSubmit={handleSubmit}>
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g. Spinach, Eggs, Avocado..."
      />

      <button className="input-btn" type="submit" disabled={loading}>
        {loading ? "Building..." : "Suggest Meals"}
      </button>
    </form>
  );
}
