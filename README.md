# University of Porto Timetable Scrapper - *UPTS*
Python solution to extract the courses schedules from the different Faculties of University of Porto.

## Requirements
- docker-ce
- docker-compose

## Run
### Main computer
- `docker-compose build`
- `docker-compose up`
- Wait for MySQL to initialize
- `docker-compose run scrapper bash`
### Scrapper image
- `scrapy crawl faculties`
- `scrapy crawl courses`
- ~~`scrapy crawl classes -a user=xxx`~~
- `scrapy crawl courseUnits -a user=xxx`
- `scrapy crawl schedules -a user=xxx`

To inspect the scrapy engine, use `scrapy shell "url"`

Example:
```
root@00723f950c71:/scrapper# scrapy shell "https://sigarra.up.pt/fcnaup/pt/cur_geral.cur_planos_estudos_view?pv_plano_id=2523&pv_ano_lectivo=2017&pv_tipo_cur_sigla=D&pv_origem=CUR"
2017-10-24 20:51:35 [scrapy.utils.log] INFO: Scrapy 1.4.0 started (bot: scrapper)
...
>>> open('dump.html', 'wb').write(response.body)
63480
>>> response.xpath('//*[@id="anos_curr_div"]/div').extract()
```
