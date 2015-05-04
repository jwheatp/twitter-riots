library(ggplot2)
library(xts)
library(scales)

args <- commandArgs(trailingOnly = TRUE)

path = toString(args[1])

data = read.csv(file="../../data/tweets/tweets_fw_10_08_p",header=F,sep=',',quote='\"')

data["tagged"] = 1

head(data)

data$V11 = tolower(data$V11)

data[(data$V11 == "ferguson"),]$tagged = 0
data[(data$V11 == ""),]$tagged = 0
data[data$tagged == 1,]$V11

untagged = data[data$tagged == 0,]
tagged = data[data$tagged == 1,]


process <- function(data) {
  data$V2 <- as.POSIXct(data$V2,format="%Y-%m-%d %H:%M:%S")
  xv = rep(1,length(data$V2))
  df = xts(xv,order.by=data$V2)
  endp = endpoints(df,on="minutes",k=20)
  aa = period.apply(df,sum,INDEX=endp)
  aa = cbind(rownames(as.matrix(aa)),as.vector(aa[,1]))
  aa = as.data.frame(aa)
  aa$V1 <- as.POSIXct(aa$V1)
  aa$V2 <- as.numeric(as.character(aa$V2))
  return(aa)
}

untagged_p = process(untagged)
tagged_p = process(tagged)

head(untagged_p)
head(tagged_p)

df = data.frame(untagged_p$V1,untagged_p$V2,tagged$V2)
head(df)

p <- ggplot(df, aes(tagged_p$V1)) + labs(y="count",x="time") + ggtitle(path) + geom_line(aes()) + scale_x_datetime(labels=date_format("%Hh"), breaks = date_breaks("hour"))

output_p = paste(path,"_freq.png",sep="")

ggsave(plot=p,file=output_p,width=11, height=7)
