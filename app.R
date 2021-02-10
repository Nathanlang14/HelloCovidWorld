library(shiny)
library(ggplot2)
library("anytime")
library(tidyverse)
library(dplyr)

#devtools::install_github("UrbanInstitute/urbnmapr")
#install.packages("ubrnmapr")
library(urbnmapr)

df <- read.csv(file = 'covid_2020_daily.csv')
head(df)

df$date <- anytime::anydate(df$date)

choices <- c("All States")

choices = append(choices, unique(df$state))

us_total <- aggregate(df[c("death","hospitalized","negative","positive","totalTestResults")],
                      by=df["date"], sum)

ui <- fluidPage (
  titlePanel(title = h2("US COVID-19 Data", align="left")),
  
  selectInput(
    inputId = "dropdownSelection",
    label = "Positive and Total Cases by State",
    choices = choices,
    selected = "All States"
  ),
  
  plotOutput("barTotals"),

  sliderInput(
    "covid_date",
    "Date:",
    min = as.Date("2020-01-13","%Y-%m-%d"),
    max = as.Date("2021-01-01","%Y-%m-%d"),
    value=as.Date("2020-04-01"),
    timeFormat="%b"
  ),
  
  plotOutput("heatmapUS")
  
)

server <- function(input, output) {
  ddSelection <- reactive(input$dropdownSelection)
  
  output$barTotals <- renderPlot({
    if (ddSelection()=="All States"){data_bar = us_total}
    else{data_bar = subset(df, df$state == ddSelection())}
    
    ggplot(data=data_bar, aes(x=date)) +
      geom_bar(aes(y=totalTestResults), stat="identity", position ="identity", alpha=.3, fill='lightblue', color='lightblue4') +
      geom_bar(aes(y=positive), stat="identity", position="identity", alpha=.8, fill='pink', color='red') +
      xlab("Date") +
      ylab("People Count")
    
  })
  
  output$heatmapUS <- renderPlot({
    daily_data <- df$date == input$covid_date
    daily_spatial_data <- left_join(get_urbn_map("states", sf = TRUE), subset(df, daily_data), by = c("state_abbv" = "state"))
    ggplot() +
      geom_sf(daily_spatial_data,
              mapping = aes(fill = positive),
              color = "#ffffff", size = 0.25) +
      scale_fill_viridis_c(option = "inferno", direction = -1) +
      labs(fill = "Positive Cases") +
      coord_sf(datum = NA)
  })
  
}

shinyApp(ui = ui, server = server)