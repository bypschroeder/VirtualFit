import { create } from "zustand";

interface ObjState {
	obj: string | null;
	setObj: (obj: string | null) => void;
}

const useObjStore = create<ObjState>((set) => ({
	obj: null,
	setObj: (obj) => set({ obj }),
}));

export default useObjStore;
