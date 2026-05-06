import Disclaimer from "./Disclaimer";
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
    <form onSubmit={handleSubmit}>
      {/* Keep the input bar layout separate so the disclaimer renders below it. */}
      <div className="input-bar">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. Spinach, Eggs, Avocado..."
        />

        <button className="input-btn" type="submit" disabled={loading}>
          {loading ? "Building..." : "Suggest Meals"}
        </button>
      </div>
      <Disclaimer />
    </form>
  );
}
