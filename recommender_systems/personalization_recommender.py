import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class PersonalizationRecommender:
    def __init__(self, user_profiles, item_profiles):
        self.user_profiles = user_profiles
        self.item_profiles = item_profiles

    def recommend(self, user_id, top_n=10):
        user_profile = self.user_profiles[user_id].reshape(1, -1)
        similarities = cosine_similarity(user_profile, self.item_profiles)
        recommendations = similarities.argsort()[0][-top_n:]
        return recommendations

if __name__ == "__main__":
    user_profiles = np.random.rand(100, 50)
    item_profiles = np.random.rand(1000, 50)
    recommender = PersonalizationRecommender(user_profiles, item_profiles)
    recommendations = recommender.recommend(user_id=1, top_n=5)
    print(f"Top 5 Recommendations for User 1: {recommendations}")
