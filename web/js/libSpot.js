




////////////////////////////////////////////////////////////////////////////////
//
// Spot
//
////////////////////////////////////////////////////////////////////////////////

export
class Spot
{
    constructor(spotData)
    {
        this.spotData = spotData;
    }

    GetRowId()
    {
        return this.spotData['ROWID'];
    }

    GetTime()
    {
        return this.spotData['TIME'];
    }

    GetLocationTransmitter()
    {
        return {
            lat: parseFloat(this.spotData['LAT']),
            lng: parseFloat(this.spotData['LNG']),
        };
    }
    
    GetMiles()
    {
        return parseInt(this.spotData['MI']);
    }
    
    GetAltitudeFt()
    {
        return parseInt(this.spotData['ALTITUDE_FT']);
    }
    
    GetSpeedMph()
    {
        return parseInt(this.spotData['SPEED_MPH']);
    }
    
    GetTemperatureC()
    {
        return parseInt(this.spotData['TEMPERATURE_C']);
    }
    
    GetTemperatureF()
    {
        return Math.round((this.GetTemperatureC() * 9.0 / 5.0) + 32);
    }
    
    GetVoltage()
    {
        return parseInt(this.spotData['VOLTAGE']);
    }
    
    GetReporter()
    {
        return this.spotData['REPORTER'];
    }
    
    GetLocationReporter()
    {
        return {
            lat: parseFloat(this.spotData['RLAT']),
            lng: parseFloat(this.spotData['RLNG']),
        };
    }
    
    GetSNR()
    {
        return this.spotData['SNR'];
    }
    
    GetFrequency()
    {
        return this.spotData['FREQUENCY'];
    }
    
    GetDrift()
    {
        return this.spotData['DRIFT'];
    }
}















