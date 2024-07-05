library(ggplot2)

data <- read.csv("data.csv")

summary_stats <- summary(data)
print(summary_stats)

ggplot(data, aes(x=Variable1, y=Variable2)) +
  geom_point() +
  theme_minimal()
