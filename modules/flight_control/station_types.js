// ESM module: station types
/**
 * JSDoc typedefs for flight control data models.
 * These mirror the design spec for DockBay, CraftProfile, TrafficSlot, MissionPlan, FuelLedger, MaintenanceTask, StationState.
 */

/** @typedef {Object} DockBay
 * @property {string} id
 * @property {string} type
 * @property {string[]} compatibleClasses
 * @property {string} status
 * @property {string} atmosphere
 * @property {{power:boolean,fuel:boolean,data:boolean}} umbilicals
 * @property {{fireReady:boolean,isolationDoor:boolean,evaOpen:boolean}} safety
 * @property {{craftId:string,since:number}=} occupancy
 * @property {number=} turnaroundETA
 * @property {string=} notes
 */

/** @typedef {Object} CraftProfile
 * @property {string} id
 * @property {string} class
 * @property {{length:number,width:number,height:number}} dimensions
 * @property {number} massKg
 * @property {string} portType
 * @property {string} fuelType
 * @property {number} maxRCS
 * @property {string[]} capabilities
 * @property {string} status
 * @property {number=} maintenanceDueAt
 */

/** @typedef {Object} TrafficSlot
 * @property {string} slotId
 * @property {{start:number,end:number}} window
 * @property {string} op
 * @property {string} corridor
 * @property {string=} assignedCraftId
 * @property {string} priority
 * @property {string} status
 */

/** @typedef {Object} MissionPlan
 * @property {string} missionId
 * @property {string} craftId
 * @property {string} opType
 * @property {{origin:string,destination:string,alternates?:string[]}} route
 * @property {{requiredKg:number,reserveKg:number}} fuelPlan
 * @property {{weather:number,debris:number,traffic:number}} riskBands
 * @property {number} etaMs
 * @property {{maxWaitMs?:number,mustUseDock?:string,auditLock?:boolean}=} constraints
 */

/** @typedef {Object} FuelLedgerEntry
 * @property {string} id
 * @property {number} ts
 * @property {string} craftId
 * @property {string} type
 * @property {string} fuelType
 * @property {number} kg
 * @property {string} by
 */

/** @typedef {Object} FuelTank
 * @property {string} fuelType
 * @property {number} capacityKg
 * @property {number} availableKg
 */

/** @typedef {Object} FuelLedger
 * @property {FuelLedgerEntry[]} entries
 * @property {FuelTank[]} tanks
 * @property {{minReserveKg:number,maxIssuePerOpKg:number}} rules
 */

/** @typedef {Object} MaintenanceTask
 * @property {string} taskId
 * @property {string} craftId
 * @property {string} template
 * @property {{hours:number,skills:string[],parts:string[]}} required
 * @property {string} status
 * @property {number=} dueBy
 * @property {boolean} deferralAllowed
 * @property {string=} notes
 */

/** @typedef {Object} StationState
 * @property {string} stationId
 * @property {number} time
 * @property {DockBay[]} docks
 * @property {CraftProfile[]} craft
 * @property {TrafficSlot[]} traffic
 * @property {MissionPlan[]} missions
 * @property {FuelLedger} fuel
 * @property {MaintenanceTask[]} maintenance
 * @property {{isolationActive:boolean,activeAlerts:string[]}} safety
 * @property {{schedulerLagMs:number,backpressure:number}} ops
 * @property {{trust:string,chain:string}} anchors
 */

// Simple factory for initial state
export function createInitialStationState() {
  return {
    stationId: "ORION_STATION_ALPHA",
    time: Date.now(),
    docks: [],
    craft: [],
    traffic: [],
    missions: [],
    fuel: { entries: [], tanks: [{ fuelType: "LH2", capacityKg: 50000, availableKg: 50000 }], rules: { minReserveKg: 500, maxIssuePerOpKg: 8000 } },
    maintenance: [],
    safety: { isolationActive: false, activeAlerts: [] },
    ops: { schedulerLagMs: 0, backpressure: 0 },
    anchors: { trust: "SN1-AS3", chain: "001//999//" },
  };
}

