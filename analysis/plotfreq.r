library(ggplot2)
library(xts)
library(scales)

args <- commandArgs(trailingOnly = TRUE)

path = toString(args[1])

data = read.csv(file=path,header=F,sep=",",quote="\"")


data$V2 <- as.POSIXct(data$V2,format="%Y-%m-%d %H:%M:%S")

xv = rep(1,length(data$V2))

df = xts(xv,order.by=data$V2)

endp = endpoints(df,on="minutes",k=20)

aa = period.apply(df,sum,INDEX=endp)


aa = cbind(rownames(as.matrix(aa)),as.vector(aa[,1]))

aa = as.data.frame(aa)

aa$V1 <- as.POSIXct(aa$V1)
aa$V2 <- as.numeric(as.character(aa$V2))

p <- ggplot(aa, aes(aa$V1,aa$V2)) + labs(y="count",x="time") + ggtitle(path) + geom_line() + scale_x_datetime(labels=date_format("%Hh"), breaks = date_breaks("hour"))

output_p = paste(path,"_freq.png",sep="")

ggsave(plot=p,file=output_p,width=11, height=7)

