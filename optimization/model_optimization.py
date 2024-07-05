import numpy as np

class ModelOptimization:
    def __init__(self, model):
        self.model = model

    def grid_search(self, param_grid):
        best_params = None
        best_score = -np.inf
        for params in param_grid:
            self.model.set_params(**params)
            score = self.model.evaluate()
            if score > best_score:
                best_score = score
                best_params = params
        return best_params

if __name__ == "__main__":
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier()
    param_grid = [{'n_estimators': [10, 50, 100], 'max_depth': [None, 10, 20]}]
    optimizer = ModelOptimization(model)
    best_params = optimizer.grid_search(param_grid)
    print(f"Best Parameters: {best_params}")
