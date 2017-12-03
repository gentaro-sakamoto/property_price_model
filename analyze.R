# install.packages(c('ggplot2',  dplyr',  'maptools',  'randomForest',  'ggrepel',  'psych'))
warnings()
library(ggplot2)
library(dplyr)
library(maptools)
library(randomForest)
library(ggrepel)
library(psych)

setwd('~/projects/property_price_model')
df <- read.csv('data/preprocessed_properties.csv',  header=T,  fileEncoding = 'UTF-8')

# Factorlize
df$plan_max <- as.factor(df$plan_max)
df$plan_min <- as.factor(df$plan_min)

options(scipen=100)
df1 <- df %>%
    select(address1) %>%
    group_by(address1) %>%
    tally() %>%
    arrange((n))

df1$address1 <- as.character(df1$address1)
df1$address1 <- factor(df1$address1,  levels = unique(df1$address1))

ggplot(df1,  aes(address1,  n)) +
  geom_bar(stat="identity") +
  ggtitle('Properties by city') +xlab('') + ylab('Properties') +
  theme(axis.text.x = element_text(angle = 0,  hjust =1)) +
  coord_flip() +
  scale_y_continuous(labels = scales::comma)

df_tokyo_pop_area <- read.csv('data/tokyo_pop_area.csv',  header=T,  fileEncoding = 'UTF-8')
df1 <- merge(df1, df_tokyo_pop_area, by="address1")
ggplot(df1, aes(population,n)) +
  geom_point() +
  ggtitle("Properties vs Population") + xlab("Population") + ylab("Properties")+
  geom_text_repel(label = df1$address1, size = 3) +
  ylim(0,25000) + scale_y_continuous(labels = scales::comma)

cor(df1$n, df1$population)

by_price_mean_median <- with(df, reorder(address1, price_mean, median))
head(by_price_mean_median)
par(las=1, cex.axis=0.7)
boxplot(price_mean ~ by_price_mean_median, data = df,
        xlab = "Price mean", ylab = "",
        main = "Price by city", varwidth = TRUE, horizontal=TRUE)
