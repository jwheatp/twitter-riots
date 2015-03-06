library(wordcloud)

args <- commandArgs(trailingOnly = TRUE)

path = toString(args[1])
out = toString(args[2])

data = read.csv(file=path,header=F,sep=",")

tbl <- table(data$V1)
tbl = cbind(Freq=tbl)
tbl = as.data.frame(tbl)
png(out,width=1400,heigh=900)
wordcloud(rownames(tbl),tbl$Freq)

