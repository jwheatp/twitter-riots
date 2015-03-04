library(maps)
data(us.cities)

ferg = c("Ferguson MO","MO","1000000","38.74","-90.30", "2")
ferg = as.data.frame(t(as.matrix(ferg)))
colnames(ferg) <- c("name","country.etc","pop","lat","long","capital")
ferg$name = toString(ferg$name)
ferg$country.etc = toString(ferg$country.etc)
ferg$pop = as.integer(as.character(ferg$pop))
ferg$lat = as.numeric(as.character(ferg$lat))
ferg$long = as.numeric(as.character(ferg$long))
ferg$capital = as.numeric(as.character(ferg$capital))

data = read.table(file="../../data/geo_fw_14_08",header=F,sep=",")

png(file="map_us.png",width=1440,height=900)

map('state', col = palette())

points(data$V1, data$V2, col = "red", cex = .6)

map.cities(us.cities, minpop=700000, cex = 2.5)

png(file="map_world.png",width=1440,height=900)

map('world', plot = TRUE, fill = FALSE, col = palette())

points(data$V1, data$V2, col = "red", cex = .6)
