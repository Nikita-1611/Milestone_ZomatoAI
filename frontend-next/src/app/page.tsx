"use client";

import { useEffect, useState } from "react";
import styles from "./page.module.css";

interface Recommendation {
  restaurant_name: string;
  rating: number;
  estimated_cost_for_two: number;
  cuisine: string[];
  ai_explanation: string;
}

interface ResultsData {
  summary: string;
  recommendations: Recommendation[];
}

const FOOD_IMAGES = [
  "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=400&h=300&fit=crop",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400&h=300&fit=crop",
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=400&h=300&fit=crop",
  "https://images.unsplash.com/photo-1565958011703-44f9829ba187?w=400&h=300&fit=crop",
  "https://images.unsplash.com/photo-1499028344343-cd173ffc68a9?w=400&h=300&fit=crop",
  "https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=400&h=300&fit=crop"
];

export default function Home() {
  const [locations, setLocations] = useState<string[]>([]);
  const [loadingLocations, setLoadingLocations] = useState(true);
  
  const [location, setLocation] = useState("");
  const [preferences, setPreferences] = useState("");
  
  // Filters
  const [budget, setBudget] = useState("1000");
  const [cuisines, setCuisines] = useState("");
  const [minRating, setMinRating] = useState("4.0");

  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<ResultsData | null>(null);

  useEffect(() => {
    async function fetchLocations() {
      try {
        const res = await fetch("/v1/locations");
        if (!res.ok) throw new Error("Failed to load locations");
        const data = await res.json();
        setLocations(data);
        if (data.length > 0) setLocation(data[0]);
      } catch (err) {
        console.error(err);
      } finally {
        setLoadingLocations(false);
      }
    }
    fetchLocations();
  }, []);

  const handleSearch = async () => {
    if (!location) return;
    
    setLoading(true);
    setError(null);
    setResults(null);
    setSearched(true);

    const parsedCuisines = cuisines
      .split(",")
      .map((c) => c.trim())
      .filter(Boolean)
      .slice(0, 5);

    const payload = {
      location,
      budget: Number(budget) || 1000,
      cuisines: parsedCuisines.length ? parsedCuisines : ["Any"],
      min_rating: Number(minRating) || 0,
      additional_preferences: preferences.trim() || null,
    };

    try {
      const res = await fetch("/v1/recommendations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        setError(typeof data === "object" ? JSON.stringify(data, null, 2) : String(data));
        return;
      }
      setResults(data);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className={styles.header}>
        <div className={styles.logo}>zomato</div>
        <nav className={styles.headerLinks}>
          <a href="#">Log in</a>
          <a href="#">Sign up</a>
        </nav>
      </header>

      <section className={styles.hero}>
        <div className={styles.heroOverlay}></div>
        <div className={styles.heroContent}>
          <h1 className={styles.heroTitle}>
            Find Your Perfect Restaurant <br />
            <span className={styles.heroTitleHighlight}>with AI</span>
          </h1>

          <div className={styles.searchPill}>
            <div className={styles.pillInputGroup}>
              <span style={{color: "var(--primary-color)", fontSize: "1.2rem"}}>📍</span>
              <select 
                className={styles.pillSelect}
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                disabled={loadingLocations}
              >
                {loadingLocations ? (
                  <option value="" disabled>Loading...</option>
                ) : (
                  locations.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))
                )}
              </select>
            </div>
            
            <div className={styles.pillInputGroup}>
              <span style={{color: "var(--text-muted)", fontSize: "1.2rem"}}>🔍</span>
              <input
                className={styles.pillInput}
                type="text"
                placeholder="Type your cravings (e.g., romantic rooftop cafe)"
                value={preferences}
                onChange={(e) => setPreferences(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
          </div>
        </div>
      </section>

      <main className={styles.container}>
        <div className={styles.filtersBar}>
          <div className={styles.filterBtn}>
            <span>Budget: ₹</span>
            <input 
              type="number" 
              style={{border: "none", width: "60px", outline: "none", fontSize: "1rem"}}
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              step="100"
            />
          </div>
          
          <div className={styles.filterBtn}>
            <span>Rating: </span>
            <input 
              type="number" 
              style={{border: "none", width: "40px", outline: "none", fontSize: "1rem"}}
              value={minRating}
              onChange={(e) => setMinRating(e.target.value)}
              min="0" max="5" step="0.5"
            />
            <span>+</span>
          </div>

          <div className={styles.filterBtn}>
            <input 
              type="text" 
              placeholder="Cuisine (e.g. Italian)"
              style={{border: "none", width: "120px", outline: "none", fontSize: "1rem"}}
              value={cuisines}
              onChange={(e) => setCuisines(e.target.value)}
            />
          </div>

          <button className={styles.actionBtn} onClick={handleSearch} disabled={loading || !location}>
            {loading ? <><span className={styles.loader}></span> Searching</> : "Get AI Recommendations"}
          </button>
        </div>

        {error && (
          <div className={styles.error}>
            Failed to fetch recommendations: {error}
          </div>
        )}

        {searched && !loading && !error && results && results.recommendations.length === 0 && (
          <div style={{textAlign: "center", padding: "40px", color: "var(--text-muted)"}}>
            <h3>No results found</h3>
            <p>Try tweaking your filters or preferences.</p>
          </div>
        )}

        {results && results.recommendations.length > 0 && (
          <div className={styles.grid}>
            {results.recommendations.map((item, idx) => (
              <div key={idx} className={styles.card}>
                <div 
                  className={styles.cardImagePlaceholder}
                  style={{ backgroundImage: `url(${FOOD_IMAGES[idx % FOOD_IMAGES.length]})`, backgroundSize: 'cover', backgroundPosition: 'center' }}
                ></div>
                <div className={styles.cardContent}>
                  
                  <div className={styles.cardHeader}>
                    <h3 className={styles.restaurantName} title={item.restaurant_name}>
                      {item.restaurant_name}
                    </h3>
                    <div className={styles.ratingBadge}>
                      {item.rating ?? "N/A"} ★
                    </div>
                  </div>

                  <div className={styles.subHeading}>
                    <span className={styles.cuisines}>
                      {item.cuisine ? item.cuisine.join(", ") : "Various"}
                    </span>
                    <span>•</span>
                    <span>₹{item.estimated_cost_for_two ?? "N/A"} for two</span>
                  </div>

                  <div className={styles.divider}></div>

                  <div className={styles.aiInsight}>
                    <strong>AI Insight:</strong> {
                      item.ai_explanation.includes("Fallback ranking") || item.ai_explanation.includes("score ")
                        ? `Looking for ${item.cuisine && item.cuisine.length > 0 ? item.cuisine[0] : 'delicious'} food? ${item.restaurant_name} offers a fantastic culinary experience for around ₹${item.estimated_cost_for_two} for two, making it the perfect spot for your next outing!`
                        : item.ai_explanation
                    }
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
