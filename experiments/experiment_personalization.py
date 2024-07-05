from recommender_systems.personalization_recommender import PersonalizationRecommender
import numpy as np

def run_experiment():
    user_profiles = np.random.rand(100, 50)
    item_profiles = np.random.rand(1000, 50)
    recommender = PersonalizationRecommender(user_profiles, item_profiles)
    recommendations = recommender.recommend(user_id=1, top_n=5)
    print(f"Top 5 Recommendations for User 1: {recommendations}")

if __name__ == "__main__":
    run_experiment()
