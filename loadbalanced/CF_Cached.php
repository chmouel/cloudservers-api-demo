<?php
require_once("php-cloudfiles/cloudfiles.php");
include("/etc/apidemo-config.php");

class Caching {
    //In Seconds
    var $cacheTime;
    
    var $filePath = "";
    var $container = "";
    var $object = "";

    function __construct($filePath, $container, $object) {
        $this->cacheTime = $GLOBALS['CACHE_TIME'];

        //check if the file path and api URI are specified, if not: break out of construct.
        if (strlen($filePath) > 0 && strlen($object) > 0 && strlen($container) > 0) {
            //set the local file path and api path
            $this->filePath = $filePath;
            $this->container = $container;
            $this->object = $object;
            if ($this->checkForRenewal()) {
                $obj = $this->getExternalInfo();
            } else {
                return true;
            }
        } else {
            echo "No file path and / or object API URI specified.";
            return false;
        }
    }

    function checkForRenewal() {
        if (!file_exists($this->filePath))
            return true;
        $filetimemod = filemtime($this->filePath) + $this->cacheTime;

        if ($filetimemod < time()) {
            return true;
        } else {
            return false;
        }
    }

    function getExternalInfo() {
        $auth = new CF_Authentication($GLOBALS['USER'],
                                      $GLOBALS['API_KEY'],
                                      NULL,
                                      $GLOBALS['AUTH_SERVER']);
        $auth->authenticate();
        $conn = new CF_Connection($auth, $servicenet=True);
        $cont = $conn->get_container($this->container);
        $obj = $cont->get_object($this->object);
        $obj->save_to_filename($this->filePath);
        return True;
    }
}

try {
    $t = new Caching($FILE, $CONTAINER, $OBJECT);
    echo file_get_contents($FILE);
} catch (Exception $e) {
    echo "<b>Error:</b><i>There was a problem with the CloudFiles access</i>";
    echo "<pre>$e</pre>";
}

?>
