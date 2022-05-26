using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

namespace amsiscan
{

    class Program
    {
        static byte[] FileToByteArray(string fileName)
        {
            byte[] buff = null;
            FileStream fs = new FileStream(fileName,
                                           FileMode.Open,
                                           FileAccess.Read);
            BinaryReader br = new BinaryReader(fs);
            long numBytes = new FileInfo(fileName).Length;
            buff = br.ReadBytes((int)numBytes);
            return buff;
        }

        static void Main(string[] args)
        {
            var virus = FileToByteArray(args[0]);

            IntPtr context;
            var hrInit = AmsiInitialize("AmsiTest", out context);
            if (hrInit != 0)
            {
                Console.WriteLine($"AmsiInitialize failed, HRESULT {hrInit:X8}");
                return;
            }

            AMSI_RESULT result;
            var hrScan = AmsiScanBuffer(
                context, virus, (uint)virus.Length,
                "EICAR Test File", IntPtr.Zero, out result
            );

            AmsiUninitialize(context);

            if (hrScan != 0)
            {
                Console.WriteLine($"AmsiScanBuffer failed, HRESULT {hrScan:X8}");
            }
            else if (result == AMSI_RESULT.AMSI_RESULT_DETECTED)
            {
                Console.WriteLine("Result: Detected");
            }
            else
            {
                Console.WriteLine($"Result: Not detected ({result})");
            }

        }

        public enum AMSI_RESULT
        {
            AMSI_RESULT_CLEAN = 0,
            AMSI_RESULT_NOT_DETECTED = 1,
            AMSI_RESULT_BLOCKED_BY_ADMIN_START = 16384,
            AMSI_RESULT_BLOCKED_BY_ADMIN_END = 20479,
            AMSI_RESULT_DETECTED = 32768
        }

        [DllImport("Amsi.dll")]
        public static extern uint AmsiInitialize(
            string appName,
            out IntPtr amsiContext
        );

        [DllImport("Amsi.dll")]
        public static extern uint AmsiScanBuffer(
            IntPtr amsiContext,
            byte[] buffer,
            uint length,
            string contentName,
            IntPtr session,
            out AMSI_RESULT result
        );

        [DllImport("Amsi.dll")]
        public static extern void AmsiUninitialize(
            IntPtr amsiContext
        );
    }
}