import { create } from "zustand";

interface ObjState {
	obj: string | null;
	setObj: (obj: string | null) => void;
	isObjLoading: boolean;
	setIsObjLoading: (isObjLoading: boolean) => void;
}

const useObjStore = create<ObjState>((set) => ({
	obj: null,
	setObj: (obj) => set({ obj }),
	isObjLoading: false,
	setIsObjLoading: (isObjLoading) => set({ isObjLoading }),
}));

export default useObjStore;
