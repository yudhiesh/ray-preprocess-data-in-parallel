# preprocess-data-in-parallel-with-ray

Repository for liveProject: Preprocess Data in Parallel with Ray

#News dataset
found in the /news folder, includes a set of news which you can use to run your scraper,
the usage of live websites for scraping is not advisable, as the huge amount of HTTP calls
made at the same time by yoru script and from multiple students might cause issues to a live platform.
You will need, also, to think about how to be less invasive as possible while you do your exercise, but for now
you can practice using these news, which have been already scraped for you, and you can re-scrape doing the following actions:

- Navigate to the news folder in your machine
- type:
  ` python -m http.server 8000`

Depending on how you installed python in your system you might have to substitute _python_ with _python3_ but
make sure you have a version of python >= than 3.6

# Stage 1

Runs were completed on 2019 MacBook Pro 16 with 12 CPU Cores

## Comparison of the results

Refer to `time_results.json` which contains name of the main function run and the total time it took for it to run.
This json file is updated and run through the [@timing decorator](https://github.com/manning-lp/yudhiesh-preprocess-data-in-parallel-lp/blob/b8593b7e2b19f1ab2f3394fba0227ae483d9d509/src/utils.py#L13).

I have two versions being stored currently(will add another for the Ray + asyncio version):

1. Synchronous version takes 1600 seconds to run(`python src/web_scraper/main.py sync run`)
2. Asynchronous + Multiprocessing version takes 335 seconds to run(`python src/web_scraper/main.py async run --semaphore-count 50`)
3. Ray implementation takes roughly 12.3 seconds to run(`python src/web_scraper/main.py sync_ray run`)

# Stage 2

## Comparison of the results

Refer to `time_results_file.json` which contains name of the main function run and the total time it took for it to run.

I have two versions being stored currently:

1. `main_file_processor` takes 3160 seconds to run(base synchronous version)
2. `main_file_processor_ray` takes rought 64 seconds to run(Ray parallelising processing function)
