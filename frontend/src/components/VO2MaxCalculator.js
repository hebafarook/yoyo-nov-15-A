import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Calculator, Heart, Activity, ExternalLink, Bookmark } from 'lucide-react';

const VO2MaxCalculator = ({ onCalculate, currentAge, currentGender, onSaveBenchmark }) => {
  const [calculatorData, setCalculatorData] = useState({
    age: currentAge || '',
    gender: currentGender || 'male',
    restingHeartRate: '',
    maxHeartRate: '',
    calculatedVO2Max: null,
    lastCalculation: null
  });

  const [benchmarks, setBenchmarks] = useState([]);

  // ACSM Formula for VO2 Max calculation
  const calculateVO2Max = () => {
    const { age, gender, restingHeartRate, maxHeartRate } = calculatorData;
    
    if (!age || !restingHeartRate || !maxHeartRate) {
      alert('Please fill in all required fields');
      return;
    }

    let vo2Max;
    if (gender === 'male') {
      // For males: VO2 Max = (0.21 * Max Heart Rate) – (0.84 * Age) – (0.25 * Resting Heart Rate) + 84
      vo2Max = (0.21 * parseFloat(maxHeartRate)) - (0.84 * parseFloat(age)) - (0.25 * parseFloat(restingHeartRate)) + 84;
    } else {
      // For females: VO2 Max = (0.12 * Max Heart Rate) – (0.64 * Age) – (0.35 * Resting Heart Rate) + 65.4
      vo2Max = (0.12 * parseFloat(maxHeartRate)) - (0.64 * parseFloat(age)) - (0.35 * parseFloat(restingHeartRate)) + 65.4;
    }

    // Round to 1 decimal place
    vo2Max = Math.round(vo2Max * 10) / 10;

    const calculation = {
      vo2Max,
      timestamp: new Date().toISOString(),
      inputs: { age, gender, restingHeartRate, maxHeartRate }
    };

    setCalculatorData(prev => ({
      ...prev,
      calculatedVO2Max: vo2Max,
      lastCalculation: calculation
    }));

    // Pass the calculated value back to parent component
    if (onCalculate) {
      onCalculate(vo2Max);
    }
  };

  const saveBenchmark = async () => {
    if (!calculatorData.calculatedVO2Max) {
      alert('Please calculate VO2 Max first');
      return;
    }

    const benchmark = {
      id: Date.now().toString(),
      vo2Max: calculatorData.calculatedVO2Max,
      date: new Date().toISOString(),
      inputs: calculatorData.lastCalculation.inputs,
      notes: `Calculated using ACSM formula`
    };

    setBenchmarks(prev => [...prev, benchmark]);

    // Save to backend if function provided
    if (onSaveBenchmark) {
      await onSaveBenchmark(benchmark);
    }

    alert('Benchmark saved successfully!');
  };

  const getFitnessLevel = (vo2Max, age, gender) => {
    if (!vo2Max) return '';
    
    // Basic fitness level categorization
    if (gender === 'male') {
      if (age <= 19) {
        if (vo2Max >= 56) return 'Excellent';
        if (vo2Max >= 47) return 'Good';
        if (vo2Max >= 37) return 'Average';
        return 'Below Average';
      } else if (age <= 29) {
        if (vo2Max >= 52) return 'Excellent';
        if (vo2Max >= 43) return 'Good';
        if (vo2Max >= 33) return 'Average';
        return 'Below Average';
      }
    } else {
      if (age <= 19) {
        if (vo2Max >= 48) return 'Excellent';
        if (vo2Max >= 39) return 'Good';
        if (vo2Max >= 29) return 'Average';
        return 'Below Average';
      } else if (age <= 29) {
        if (vo2Max >= 44) return 'Excellent';
        if (vo2Max >= 35) return 'Good';
        if (vo2Max >= 25) return 'Average';
        return 'Below Average';
      }
    }
    return 'Average';
  };

  const handleInputChange = (field, value) => {
    setCalculatorData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Card className="vo2-calculator-card">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Calculator className="w-5 h-5" />
          VO2 Max Calculator
          <a 
            href="https://sporthypnosis.net/elementor-1032/" 
            target="_blank" 
            rel="noopener noreferrer"
            className="ml-2 text-blue-600 hover:text-blue-800"
            title="View original calculator"
          >
            <ExternalLink className="w-4 h-4" />
          </a>
        </CardTitle>
        <p className="text-sm text-gray-600">
          Calculate your VO2 Max using ACSM (American College of Sports Medicine) formulas
        </p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Basic Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-sm font-medium">Age</Label>
            <Input
              type="number"
              value={calculatorData.age}
              onChange={(e) => handleInputChange('age', e.target.value)}
              placeholder="Enter age"
              className="mt-1"
            />
          </div>
          
          <div>
            <Label className="text-sm font-medium">Gender</Label>
            <select
              value={calculatorData.gender}
              onChange={(e) => handleInputChange('gender', e.target.value)}
              className="mt-1 w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
        </div>

        {/* Heart Rate Data */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label className="text-sm font-medium flex items-center gap-1">
              <Heart className="w-4 h-4" />
              Resting Heart Rate (bpm)
            </Label>
            <Input
              type="number"
              value={calculatorData.restingHeartRate}
              onChange={(e) => handleInputChange('restingHeartRate', e.target.value)}
              placeholder="e.g., 60"
              className="mt-1"
            />
          </div>
          
          <div>
            <Label className="text-sm font-medium flex items-center gap-1">
              <Activity className="w-4 h-4" />
              Max Heart Rate (bpm)
            </Label>
            <Input
              type="number"
              value={calculatorData.maxHeartRate}
              onChange={(e) => handleInputChange('maxHeartRate', e.target.value)}
              placeholder="e.g., 190"
              className="mt-1"
            />
          </div>
        </div>

        {/* Calculate Button */}
        <Button 
          onClick={calculateVO2Max}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white"
        >
          <Calculator className="w-4 h-4 mr-2" />
          Calculate VO2 Max
        </Button>

        {/* Results */}
        {calculatorData.calculatedVO2Max && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-green-800 mb-2">
                Your VO2 Max Result
              </h3>
              <div className="text-3xl font-bold text-green-900 mb-2">
                {calculatorData.calculatedVO2Max} ml/kg/min
              </div>
              <div className="text-sm text-green-700 mb-4">
                Fitness Level: <span className="font-semibold">
                  {getFitnessLevel(calculatorData.calculatedVO2Max, calculatorData.age, calculatorData.gender)}
                </span>
              </div>
              
              <Button 
                onClick={saveBenchmark}
                variant="outline"
                className="border-green-600 text-green-700 hover:bg-green-50"
              >
                <Bookmark className="w-4 h-4 mr-2" />
                Save as Benchmark
              </Button>
            </div>
          </div>
        )}

        {/* Formula Information */}
        <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg text-xs">
          <h4 className="font-semibold mb-2">ACSM Formulas Used:</h4>
          <div className="space-y-1">
            <div><strong>Males:</strong> VO2 Max = (0.21 × Max HR) – (0.84 × Age) – (0.25 × Resting HR) + 84</div>
            <div><strong>Females:</strong> VO2 Max = (0.12 × Max HR) – (0.64 × Age) – (0.35 × Resting HR) + 65.4</div>
          </div>
          <p className="mt-2 text-gray-600">
            Note: This is an estimation. Laboratory testing provides more accurate results.
          </p>
        </div>

        {/* Saved Benchmarks */}
        {benchmarks.length > 0 && (
          <div className="mt-4">
            <h4 className="font-semibold mb-2">Saved Benchmarks</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {benchmarks.map((benchmark) => (
                <div key={benchmark.id} className="text-xs p-2 bg-gray-50 border rounded">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{benchmark.vo2Max} ml/kg/min</span>
                    <span className="text-gray-500">
                      {new Date(benchmark.date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default VO2MaxCalculator;