import axios from 'axios';
import csv from 'csv-parser';

class CsvDataFetcher {
    private resultIds: number[];

    constructor(resultIds: number[]) {
        this.resultIds = resultIds;
    }

    public async fetchData(): Promise<any[]> {
        const results: any[] = [];
        const url = `https://monitormywatershed.org/api/csv-values/?result_ids=${this.resultIds.join(",")}`;

        const response = await axios.get(url, { responseType: 'stream' });

        return new Promise((resolve, reject) => {
            response.data
                .pipe(csv())
                .on('data', (data) => results.push(data))
                .on('end', () => resolve(results))
                .on('error', (error) => reject(error));
        });
    }
}

class WatershedDataExtractor {
    private dataFetcher: CsvDataFetcher;

    constructor(resultIds: number[]) {
        this.dataFetcher = new CsvDataFetcher(resultIds);
    }

    public async doSomethingWithCsvData() {
        const csvData = await this.dataFetcher.fetchData();
        // Do something with csvData...
    }
}
