import axios from 'axios';
import csv from 'csv-parser';

interface Watershed {
    DateTime: string;
    TimeOffset: string;
    DateTimeUTC: string;
    Maxim_DS3231_Temp: number;
    TBRain_5Min: number;
}

class CsvDataFetcher {
    private resultIds: number[];

    constructor(resultIds: number[]) {
        this.resultIds = resultIds;
    }

    public async fetchData(): Promise<Watershed[]> {
        const results: Watershed[] = [];
        const url = `https://monitormywatershed.org/api/csv-values/?result_ids=${this.resultIds.join(",")}`;

        try {
            const response = await axios.get(url, { responseType: 'stream' });

            return new Promise((resolve, reject) => {
                response.data
                    .pipe(csv())
                    .on('data', (data: Watershed) => results.push(data))
                    .on('end', () => resolve(results))
                    .on('error', (error: any) => reject(error));
            });
        } catch (error) {
            throw new Error(`Axios request failed: ${error.message}`);
        }
    }
}
