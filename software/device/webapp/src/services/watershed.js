const csv = require('csv-parser');
const fs = require('fs');

export class Watershed {
    constructor(filename) {
        this.filename = filename;
    }

    readCSV() {
        const results = [];
        fs.createReadStream(this.filename)
            .pipe(csv({}))
            .on('data', (data) => results.push(data))
            .on('end', () => {
                console.log(results);
            });
        return results;
    }
}

const data = new Watershed("../VUW_Test_TimeSeriesResults.csv");
console.log(data.readCSV());
