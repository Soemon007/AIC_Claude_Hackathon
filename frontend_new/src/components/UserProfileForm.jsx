export default function UserProfileForm({
  profile,
  onFieldChange,
  onSave,
  saved,
}) {
  return (
    <section className="profile-card">
      <h2>Health Profile</h2>
      <p>Help us tailor your nutrition plan.</p>

      <form
        className="form-grid"
        onSubmit={(event) => {
          event.preventDefault();
          onSave();
        }}
      >
        <div className="form-group full">
          <label htmlFor="fullName">Full Name</label>
          <input
            id="fullName"
            type="text"
            value={profile.fullName}
            onChange={(event) => onFieldChange("fullName", event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="age">Age</label>
          <input
            id="age"
            type="number"
            value={profile.age}
            onChange={(event) => onFieldChange("age", event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="weightKg">Weight (kg)</label>
          <input
            id="weightKg"
            type="number"
            value={profile.weightKg}
            onChange={(event) => onFieldChange("weightKg", event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="heightCm">Height (cm)</label>
          <input
            id="heightCm"
            type="number"
            value={profile.heightCm}
            onChange={(event) => onFieldChange("heightCm", event.target.value)}
          />
        </div>

        <div className="form-group">
          <label htmlFor="activity">Activity</label>
          <select
            id="activity"
            value={profile.activity}
            onChange={(event) => onFieldChange("activity", event.target.value)}
          >
            <option value="sedentary">Sedentary</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active</option>
          </select>
        </div>

        <div className="form-group full">
          <label htmlFor="targetGoal">Goal</label>
          <select
            id="targetGoal"
            value={profile.targetGoal}
            onChange={(event) => onFieldChange("targetGoal", event.target.value)}
          >
            <option value="weight_loss">Weight Loss</option>
            <option value="energy">Energy</option>
            <option value="fertility">Fertility Support</option>
            <option value="maintenance">General PCOS Support</option>
          </select>
        </div>

        <button type="submit" className="submit-profile">
          Save Profile
        </button>
      </form>

      <p className="profile-note">
        {saved
          ? "Profile saved. Your next recommendation will use these details."
          : "Saved profile details are included in the recommendation request."}
      </p>
    </section>
  );
}
