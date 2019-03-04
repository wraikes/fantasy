library(tidyverse)
library(leaps)
options(max.print=1000000)
df <- read_csv('C:\\Users\\william.raikes\\Desktop\\personal\\fantasy\\nba\\code\\full_data.csv')

df <- df %>%
  filter(Inj!=0) %>%
  select(-Likes, -Inj, -Actual_Val, -Actual_Min, -Date)


cols <- c('L2_FGA_lag_3', 'L5_FGA_lag_3', 'S_FGA_lag_3', 'S_FP_lag_3',
   'L5_FP_lag_3', 'Actual_FP_lag_3', 'L2_FGA_lag_4', 'L5_FGA_lag_4', 'S_FGA_lag_4', 'S_FP_lag_4',
   'L5_FP_lag_4', 'Actual_FP_lag_4', 'L2_FGA_lag_5', 'L5_FGA_lag_5', 'S_FGA_lag_5', 'S_FP_lag_5',
   'L5_FP_lag_5', 'Actual_FP_lag_5')

for(col in cols){
  df[[col]] <- as.numeric(df[[col]])
}

x <- regsubsets(Actual_FP ~ .-Player_Name, data=df, method='seqrep')

model <- lm(Actual_FP ~ ., data=df)
x<-summary(model)

df$Pos <- factor(df$Pos)
df <- within(df, Pos <- relevel(Pos, ref = 'C'))
model <- lm(Actual_Val ~ .+Salary*Proj_FP+Proj_Min:Pos+Proj_FP:Pos+Proj_Val:Pos-Player_Name+Player_Name
            , data=df)


summary(model)


library(tidyverse)
options(max.print=1000000)

df <- read_csv('C:\\Users\\william.raikes\\Desktop\\personal\\fantasy\\nba\\code\\tmp_tst.csv')
head(df)
df$Pos <- factor(df$Pos)
df <- within(df, Pos <- relevel(Pos, ref = 'SF'))
model <- lm(Actual_Val ~ . - Inj - Actual_FP - Actual_Min - Date + Pos:Proj_Val + Pos:Home, data=df)
summary(model)


#optimize for C 1st; and then possibly teams.
