library(tidyverse)
library(data.table)
library(inspectdf)
library(shiny)

injuries <- fread('injuries.csv')
products <- fread('products.csv')
population <- fread('population.csv')

# Exploratory data analysis

injuries %>% glimpse()
products %>% glimpse()
population %>% glimpse()

injuries$prod_code %>% as.factor() %>% table() %>% as.data.frame() %>% 
  arrange(desc(Freq)) %>% .[1,1] -> pc

products$title[products$prod_code == pc]

stair_step <- injuries %>% filter(prod_code ==1842)

# 1
stair_step %>% count(diag, sort = T)
# 2
stair_step %>% count(body_part, sort = T)
# 3
stair_step %>% count(location, sort = T)
# 4
stair_step %>% count(age, sex) %>% 
  merge(population, by = c('age', 'sex'), all.x = T) %>% 
  mutate(rate = n / population * 10000) %>% 
  ggplot(aes(age, rate, colour = sex))+
  geom_line()+
  labs(y ='Injuries per 10000 people')


ui <- fluidPage(
  theme = shinythemes::shinytheme('flatly'),
  titlePanel(title = h1('Consumer Product Safety Commission', align = 'center'),
             windowTitle = 'DSA - Case Study'),
  fluidRow(
    column(2,
           dateRangeInput('date',
                          label = 'When the person was seen in hospital',
                          start = min(stair_step$trmt_date),
                          end = max(stair_step$trmt_date)),
           br(),
           sliderInput('age',
                       label = 'Age of patients:',
                       min = min(stair_step$age),
                       max = max(stair_step$age),
                       value = c(20, 45))
    ),
    column(5,
           h3(strong('Places where the accident occurred:')),
           plotOutput('Location_result')
    ),
    column(5,
           h3(strong('Basic diagnosis of injury:')),
           plotOutput('Diag_result')
    )
  ),
  fluidRow(
    column(7,
           h3(strong('Injuries per 10000 people:')),
           plotOutput('injuries_per_result')),
    column(5,
           h3(strong('Location of the injury on the body:')),
           plotOutput('Bodypart_result')
    )
  )
)
server <- function(input, output, session) {
  output$Location_result <- renderPlot({
    ggplot(stair_step %>%
             filter(between(trmt_date, min(input$date), max(input$date)),
                    between(age, min(input$age), max(input$age))) %>%
             count(location, sort = T), aes(x ='', y =n , fill = location))+
      geom_col(color = 'black')+ geom_text(aes(label = n),
                                           postion = position_stack(vjust = 0.5))+
      coord_polar(theta = 'y')+
      scale_fill_brewer()+theme_bw()
  })
  output$Diag_result <-  renderPlot({
    ggplot(stair_step %>%
             filter(between(trmt_date, min(input$date), max(input$date)),
                    between(age, min(input$age), max(input$age))) %>%
             count(diag, sort = T), aes(x = n , y = diag))+
      geom_col(aes(fill = diag))+
      theme(legend.position = 'none')+scale_fill_hue(c = 20)+
      geom_text(aes(label = n), vjust = 0.2, size = 3, col = 'black')
  })
  output$injuries_per_result <- renderPlot({
    stair_step %>%
      filter(between(trmt_date, min(input$date), max(input$date)),
             between(age, min(input$age), max(input$age))) %>%
      count(age, sex) %>%
      merge(population, by =c('age', 'sex'), all.x = T) %>%
      mutate(rate = n / population * 10000) %>%
      ggplot(aes(age, rate, colour = sex))+
      geom_line()
  })
  output$Bodypart_result <- renderPlot({
    ggplot(stair_step %>%
             filter(between(trmt_date, min(input$date), max(input$date)),
                    between(age, min(input$age), max(input$age))) %>%
             count(body_part, sort = T), aes(x = n , y = body_part))+
      geom_col(aes(fill = 'yellow'))+
      theme(legend.position = 'none')+scale_fill_hue(c = 20)+
      geom_text(aes(label = n), vjust = 0.2, size = 3, col = 'black')
  })
}
shinyApp(ui, server)
