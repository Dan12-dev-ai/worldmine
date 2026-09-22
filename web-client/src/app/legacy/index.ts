/**
 * World Mine — typed re-exports of legacy untyped JSX route components.
 * Isolates the `@ts-expect-error` seams here so the router stays clean;
 * each legacy screen migrates to TS in its own phase (§65/§66).
 */

// @ts-expect-error — legacy module is untyped JSX (migration map, Phase 10)
import PlanetaryUI from '../../components/PlanetaryUI';
// @ts-expect-error — legacy module is untyped JSX (migration map, Phase 10)
import GlobalSwarmDashboard from '../../components/GlobalSwarmDashboard';
// @ts-expect-error — legacy module is untyped JSX (migration map, Phase 10)
import UniversalCheckoutUI from '../../components/UniversalCheckoutUI';
// @ts-expect-error — legacy module is untyped JSX (migration map, Phase 10)
import MobileThumbZone from '../../components/MobileThumbZone';
// @ts-expect-error — legacy module is untyped JSX (migration map, Phase 10)
import LocalizationDemo from '../../components/LocalizationDemo';

export {
  PlanetaryUI,
  GlobalSwarmDashboard,
  UniversalCheckoutUI,
  MobileThumbZone,
  LocalizationDemo,
};
