evaluate_model <- function(predictions, labels) {
  accuracy <- sum(predictions == labels) / length(labels)
  precision <- sum(predictions & labels) / sum(predictions)
  recall <- sum(predictions & labels) / sum(labels)
  f1_score <- 2 * (precision * recall) / (precision + recall)
  return(list(accuracy=accuracy, precision=precision, recall=recall, f1_score=f1_score))
}

predictions <- c(TRUE, FALSE, TRUE, TRUE, FALSE)
labels <- c(TRUE, FALSE, TRUE, FALSE, TRUE)

evaluation_metrics <- evaluate_model(predictions, labels)
print(evaluation_metrics)
