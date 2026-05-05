import Navbar from "../components/NavBar";
import UserInputForm from "../components/UserInputForm";
import IngredientTags from "../components/IngredientTags";
import MealCard from "../components/Mealcard";
import UserProfileForm from "../components/UserProfileForm";
import { usePCOS } from "../hooks/UsePCOS";

export default function Home() {
  const {
    input,
    setInput,
    profile,
    setProfileField,
    saveProfile,
    profileSaved,
    result,
    error,
    loading,
    fetchMeals
  } = usePCOS();

  return (
    <>
      <Navbar />

      <main className="main-container">
        {/* LEFT */}
        <section className="search-section">
          <h1>
            Your kitchen, <em>optimized</em> for PCOS.
          </h1>

          <p className="subtitle">
            Enter ingredients and get low-GI meal suggestions.
          </p>

          <UserInputForm
            input={input}
            setInput={setInput}
            onSubmit={fetchMeals}
            loading={loading}
          />

          <IngredientTags setInput={setInput} />

          <MealCard result={result} error={error} loading={loading} />
        </section>

        {/* RIGHT */}
        <UserProfileForm
          profile={profile}
          onFieldChange={setProfileField}
          onSave={saveProfile}
          saved={profileSaved}
        />
      </main>
    </>
  );
}
