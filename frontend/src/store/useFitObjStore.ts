import { create } from "zustand";

interface FitObjState {
	fitObj: string | null;
	fitMtl: string | null;
	setFitObj: (obj: string | null) => void;
	setFitMtl: (mtl: string | null) => void;
	isFitObjLoading: boolean;
	setIsFitObjLoading: (isLoading: boolean) => void;
}

const useFitObjStore = create<FitObjState>((set) => ({
	fitObj: null,
	fitMtl: null,
	setFitObj: (fitObj) => set({ fitObj }),
	setFitMtl: (fitMtl) => set({ fitMtl }),
	isFitObjLoading: false,
	setIsFitObjLoading: (isFitObjLoading) => set({ isFitObjLoading }),
}));

export default useFitObjStore;
